# E4 wave 2 — data scaling with the new admitted rows: prepare the package (gpt-6.1-sol, xhigh, network ON read-only; NO submission except smoke jobs on `debug`)

Workspace: greek-page-ocr; new branch `sol/e4-wave2` from `sol/e4-wave1c` (ee5b40d, so the label-overlay mechanism is reused); commit there or deliver a bundle under `out/e4/wave2_prep/`; never push. Read first: `briefs/E4_wave1c_brief.md` and `bench/e4_wave1c.py`, `briefs/E4_wave1b_brief.md`, `E4_WAVE1B_RESULTS.md`, `E4_WAVE1E_RESULTS.md` (upsampling refuted), `DATA_PLAN_v2_20261016.md` §3–§4 (size × targeting design, class quotas, parliament cap 25%), and the launch lessons in `~/Projects/greek-page-ocr-wave1d/docs/ocr_program_2026-10-06/e4_wave1d/SUBMIT.md` (E4_ROOT, prepare step, smoke jobs, verify receipts).

## Owner programme (17 Oct, verbatim)
"(2) we just need to repeat the data scaling experiments with more data when sourcing is done; after we apply the right filtering and corrections if they work".

## Design (preregister; H7)
- **Control = v_c** (wave-1b recipe: codec v2 + recovered rows, width ×2, 50% synthetic v5, 8 epochs, three seeds; reuse v_c checkpoints/predictions if on Clariden and hash-verified, else retrain).
- **Arm add:** v_c's real rows PLUS every row of the admitted new-row files at natural frequency; the synthetic half recomputed to stay 50%; same draws per epoch (so this is "more unique real rows at fixed compute", the plan's size axis); parliament cap 25% re-applied after the union.
- **Arm add_corr:** add + the registered label corrections applied by row id to BOTH the old and the new rows (wave 1c overlay mechanism; versions: ru1_v2_train, n1_v1_train, sf7-rc1 marks release, whichever are registered at bind time; report which).
- **Inputs:** admission files from the sourcing track, by path + sha: now `~/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/release_admissions/w1_originals_v3.jsonl` (sha d12a7b5a895b43b515e21be1d8bc53d82ac836270f12f7a94b5762418accf5f8, 30,114 rows, original crops, arm release-v3); later `w2_originals_v3.jsonl`, the Gazette and BSB admissions, and one final `release_v3_admission.jsonl` (the bind step takes a list of files and asserts every sha). Labels are Google text through the codec v2 text policy (report rejections); crops referenced by sha (W1 crops are already on Clariden under `$W/collection_v2_masked_1d/w1/` ONLY as masked copies — do not use them; the ORIGINAL W1 crops must be uploaded, ≈16,562 + the rest of the 30,114, from `~/Projects/collect-v3-data/run/W1/crops/`; plan and hash the upload, execute it in the deploy step).
- **Instruments:** as wave 1b plus the per-class and per-line-type slices (E3 instrument set: all-caps, numerics, punctuation-heavy, mixed, Cyrillic), the locked new-source strata (ii) 200 and (i-b) 400 lines (original crops; ask the sourcing lead for paths by reference) as `newsource_locked`, and the changed-label test slice from wave 1c for add_corr.
- **H7:** add lowers v2_test CER overall and on the weak categories beyond v_c's three-seed range; add_corr lowers it further on the corrected classes; refuted otherwise. Driver computes the verdicts. MIX_TABLE receipt (previous vs new unique rows and draw shares per class) is mandatory.

## Deliverables
1. `bench/e4_wave2.py` + tests (admission-file union by row id with sha assertions, parliament cap, synthetic recompute, overlay reuse, draw contract, MIX_TABLE).
2. sbatch/submit flow per the wave-1d pattern (E4_ROOT, prepare, smoke mode, verify receipts, SUBMIT.md).
3. Local CPU mock with the current W1 file; DEPLOY lists and hashes; upload plan with bytes for the original W1 crops; nothing deployed or uploaded until I say (the final admission file arrives tomorrow).
4. `briefs/E4_wave2_readback_brief.md`; registry rows in `TRAINING_DIRECTIONS_20261016.md` ("preregistered 17 Oct", wave 2, H7).

Hand-off: `out/e4/wave2_prep/HANDOFF.md`; last line exactly:
`E4-2 PREP: done | arms: ctrl/add/add_corr | admitted rows bound (mock): <n> | upload plan: <GB> | tests: <n> passed | commit: <sha|bundle>`

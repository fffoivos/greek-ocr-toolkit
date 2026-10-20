# MIX1C: bind the final wave-2 loader; E1/A12 clone_build derivatives; draw once in the index form; requalify EXPORT (gpt-6.1-sol, medium, network ON for read-only `ssh clariden` and the final deploy `rsync` only, no spend, no jobs)

The base is MIX1B (commit 783e6597d, `mix1/`, package `mix1_pkg/c6f7e628`). Arms M1–M4 are qualified and EXPORT is stopped on three loader gaps. The training lead ("Segmentation and secondary corrections") and the coordinator have now resolved those gaps. Implement exactly the following; change nothing else in the arms and add no filters. `W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3`.

## Resolutions to implement
1. **The final wave-2 loader package.**
   - Bind `$W/e4_wave2_rel3_20261020/code/27a49e51fa735e8f`:
     - code commit `c5841ba` on `opus/e4-wave2-rel3`;
     - local worktree `~/Projects/greek-page-ocr-e4w2`, read-only;
     - `DEPLOY_RECEIPT.json` manifest_sha256 `27a49e51fa735e8f064fa68a2da2c5fda7dcefa0e54eecd0b3bc41664b1f1457` (receipt commit field `27b9cd1…`).
   - Do **not** bind `4537ef9d` or `efe9f501`.
   - Check that the local and deployed bytes of codec v2.1, `train/mix.py`, `bench/e4_codec_release.py` and the factory binary/import path you use are equal.
   - Loader change compared with cdd2004: `validate()` was split into `validate_metadata()` + full `validate()`. `load_rows`/`assemble`/`clone_build` are unchanged. Use the full `validate()` in the round trip; `validate_metadata()` may serve as VERIFY's light pre-check.
2. **Codec custody for E1 and A12.**
   - Make **our own** v2.1 derivatives using the training lead's `bench/e4_codec_release.py clone_build(source, target, codec_path=codec/v2.1)`, unchanged, under the MIX1 export's own prep dir. It changes only the `codec_version` column and asserts every other column equal. Label_ids are not re-encoded: the codec policy is append-only.
   - Each derivative gets an `encoding_derivation` receipt binding the source build_info sha + codec sha. The sources stay bound in place and untouched.
   - **The A12 cross-check is pending:** once the training lead says inventory03 has completed, compare with `$W/e4_wave2_rel3_20261020/preparation/inventory03/control_synthetic_7/build_info.json`:
     - equal `encoding_derivation` `source_receipt_sha256` + `codec_sha256` is the contract;
     - equal shard_inventory sha is a bonus;
     - if the bytes differ, report column-level equality.
   - Implement that comparison as a VERIFY mode (`crosscheck-a12 <path>`) that reports `pending` until it is run. Their run root is never an input.
3. **Manifests: draw once, in the final form.** No draws of record exist: job 3705237 was cancelled before it started.
   - The manifests job emits, per arm, gz JSONL rows `[epoch, position, component, pool_index, line_id]`, with a header/receipt binding the pool shas, D per epoch (428,872), 8 epochs and the seed provenance (20261015). This is the training lead's form from `bench/e4_wave1c.py:174-221`.
   - **Run their existing verifier logic on our output**, imported unchanged from the bound package. If it cannot be imported without side effects, replicate the byte check exactly and cite the lines.
   - The arm draw logic stays exactly as in MIX1B.
4. **EXPORT:** one shared real v2.1 shard set of 364,871 rows, from ref_364871 (receipt `467566a7…`), through their factory binary + `encode_admissions`, unchanged.
   - The per-arm index manifests reference the shared real shards and the E1/A12 v2.1 derivatives.
   - Re-run the **1,000-row real round trip** (all three parents) against the final root with the full `validate()` and `load_rows`; it must pass. Quote the result.
5. **The fixed-draw reader** lives in the S1 training package (coordinator decision), not in MIX1. Update `LOADER_CONTRACT.md`:
   - gaps 1–2 resolved;
   - gap 3 assigned to S1 as an opt-in entry point consuming this index form;
   - the A12 cross-check pending.
6. **The account directive:** `#SBATCH --account=a0140` goes in **every** sbatch file. Job 3705237's first submit failed without it. `VERIFY.sh package` must fail if any sbatch lacks account, partition or time. Add a test for that.

## Rules
- The real-data rule stays: VERIFY fails without the real-sample receipt. It now also needs the round-trip receipt against `27a49e51`.
- Deploy to a **new** `$W/scaling_w3/mix1_pkg/<sha8>/`, leaving earlier roots as they are, and read every sha back. Run VERIFY package and VERIFY inputs; do not use `--full` on the login node.
- Write `MIX1.md`:
  - a MIX1C section;
  - **the exact coordinator block**: the manifests job, then the export job with `afterok`. No `SBATCH_ACCOUNT` workaround should be needed.
  - sizing;
  - the pending A12 cross-check.
- Tests: index-form round trip through their verifier; clone_build derivative receipt; the sbatch directive check; and every existing test.

Write a guarded commit list. Do not run `git add` or `git commit`.

The last line must be exactly:
`MIX1C: done | loader 27a49e51 bound (local=deployed) | E1/A12 clone_build v2.1 derivatives (A12 crosscheck pending) | index form verified by wave1c verifier | 1000-row round trip ok | export <ok|stopped> | package <root> VERIFY package+inputs ok | tests <n> passed | no jobs submitted`

## Lead answer to Sol's question (20 Oct): permission to write the round trip on Clariden
- **Yes.** Run the bounded 1,000-row round trip on Clariden. Write only into a **new** directory `$W/scaling_w3/mix1_scratch/roundtrip_<package sha8>/`; create it, and it must not already exist.
- **Do not delete it afterwards.** Keep it as evidence (about 22 MB) and record its path and the shas of its contents in `ROUNDTRIP_RECEIPT.json`.
- Use the login node for this 1,000-row check only. No `sbatch`/`srun`.
- Then finish the brief from step 4 onwards: qualification, deploy to the new `mix1_pkg/<sha8>/`, readback, VERIFY package and VERIFY inputs, and the same final line.

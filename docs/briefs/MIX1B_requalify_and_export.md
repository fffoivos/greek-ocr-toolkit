# MIX1B: requalify the MIX1 arms under the coordinator's rulings; bind ref_364871; add the trainer-ready EXPORT step (gpt-6.1-sol, medium, network ON for read-only `ssh clariden` and the final deploy `rsync` only, no spend, no jobs)

The base is MIX1 (commit 5842ef298, `mix1/`, diagnostic package `mix1_pkg/a72c3a44`; all four arms stopped). The coordinator ruled on 20 Oct. Implement exactly this; change nothing else and add no filters. `W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3`.

## Rulings
1. **M1 and M2, the exposure audit for E1 (A10) and synthetic v5 (A12).** Replace the edition check with a **text-exposure audit against the 2,690 seal04 references** (`$W/benchmark_0.2/seal04/benchmark_v02_{test,dev}.jsonl`, field `reference`; suite `9447f09c…`):
   - (a) an exact match after NFC + whitespace normalisation (collapse runs, strip);
   - (b) any shared normalised substring of **≥ 30 characters**.

   Drop every hit and count the hits **per source** (E1 document/source, A12 text source). Keep the key and crop-sha checks. Report the counts in the receipt.
   - Implement (b) efficiently: e.g. index every 30-character window of the 2,690 references in a set, then slide over each candidate label. State the method and its exactness.
2. **M3, dominant script** = argmax of the census `decision.final_inventory` greek/latin/cyrillic letter counts. No letters, or a tie, gives `none`, which is not Cyrillic.
   - The baseline Cyrillic share is measured on ref_364871, **including the v_c Cyrillic wave**.
   - Record that this is census evidence, not the import `script_class`.
   - If `final_inventory` is absent for some rows, count them and treat them as `none`. If more than 1% of any parent lacks it, stop M3 and report.
   - Everything else in M3 is as ruled before: reach 6% by repetition, apply the parliament 25% cap on draws first and then renormalise, and keep the capped and uncapped manifests separate.
3. **M4, waves.** There are 9 waves, W1, W2, and the v2 import `wave` field (from `$W/collection_v2/import_real_v2_train.jsonl`):
   - `parliament`, `round1`, `mixed`, `vouli`, `openarchives`, `round2`, `cyrillic`;
   - the import counts are 64,521 / 46,964 / 27,583 / 24,938 / 19,625 / 18,782 / 12,023.

   Join each v_c row to its import row by id (bind the import sha) to get the **admitted** counts in ref_364871, and put the table in the record. M4 is independent of M3. Use `p_i ∝ n_i^α` with α ∈ {1, 0.5}; apply the cap after temperature; keep the ledger.
4. **Bind ref_364871:**
   - `$W/scaling_w3/subsets/scale1-c05-003/SUBSETS_RECEIPT.json`, sha `467566a7877a6abb18af855d166ebd45597c984d5ad15f595a5f2f0d1a4414e2`;
   - `ref_364871.jsonl`, sha `0cf865f0…` (read it from the receipt).

   Complete the real-sample receipt for it: run the real code path on ≥ 1,000 real rows, or ≥ 20 per parent, and re-hash ≥ 20 real crops per parent, so that `REAL_SAMPLE_RECEIPT.json` covers 70/70 inputs.
5. **EXPORT step: trainer-ready shards and codec binding**, a new stage after the manifests.
   - Manifests list census keys. For each arm, the export writes **trainer-ready parquet shards from the ref pool**, plus a **codec binding**, with shas. It must **reuse the CURRENT wave-2 package's loader/codec (v2.1)** so that Astra 4b/5b review one artefact.
   - **The current wave-2 package** is owned by the training lead (the session "Segmentation and secondary corrections"):
     - branch `opus/e4-wave2-rel3`, HEAD `cdd2004`, local worktree `~/Projects/greek-page-ocr-e4w2` (read-only);
     - deployed at `$W/e4_wave2_rel3_20261020/code/4537ef9d20a5dc3a/`.
   - **Not** the older `sol/e4-wave2` a707a36.
   - Read the codec v2.1 files, `train/mix.py`, the shard schema/loader and its census/factory label handling (see E4W2-R3G: the decoded factory label_ids are compared with census final_text) from that branch and the deployed tree. Bind their shas, and check that the local and deployed bytes are equal.
   - Write `mix1/LOADER_CONTRACT.md` covering:
     - the shard schema (columns, image encoding, label field, codec version and sha);
     - the physical-index form `[epoch, position, component, physical pool index, line_id]`;
     - how the synthetic A12 and E1 shards are referenced: bound in place, not re-encoded;
     - what the loader must verify.

     State every point that differs from the wave-2 loader. If the real pool cannot be expressed without changing the loader, stop on EXPORT and list the gap. Do not change any trainer code.
   - The export is a separate Clariden job, CPU only. Size it by the arithmetic: 364,871 real crops, read and re-encoded once into shards shared by all arms. The per-arm manifests index the shared shards; do not write one copy per arm.
6. **Real-data rule:** keep the MIX1 rule (VERIFY fails without the real-sample receipt). Also run the export code on a **real 1,000-row slice** that includes all three parents, and the loader-contract reader on its output. Do this locally, or on Clariden read-only with the output in a temporary directory under the package's own scratch; then remove that temporary directory.

## Package
- Update `mix1/`. Deploy to a **new** `$W/scaling_w3/mix1_pkg/<sha8>/`, leaving `a72c3a44` as it is, and read every sha back.
- Run `VERIFY.sh package` and `VERIFY.sh inputs` with the subset arguments; both must pass.
- Two jobs, both submitted by the coordinator: `manifests` (all arms) and then `export`, which depends on the manifests. Write `submit_mix1.sh manifests|export` and the sbatch files, with sizing arithmetic.
- `MIX1.md`:
  - the rulings as implemented;
  - the text-exposure method;
  - the 9-wave table (import counts and admitted counts);
  - the M3 baseline Cyrillic share (measured on ref_364871 by census evidence);
  - the loader contract summary;
  - **the exact coordinator command block**;
  - the owner decisions still open (C2, P1, S3, G), listed.
- Tests: the text audit (an exact hit, a ≥ 30-character substring hit, a 29-character non-hit); dominant script, including ties and none; the 9-wave join; export round trip; and every existing test.

Write a guarded commit list. Do not run `git add` or `git commit`. Touch nothing outside `mix1/` and this brief.

The last line must be exactly:
`MIX1B: done | arms M1 <ok|stopped> M2 <..> M3 <..> M4 <..> | export <ok|stopped> (wave-2 loader v2.1 <reused|gap>) | real-sample 70/70 | text-audit method <exact+30char> | package <root> VERIFY package+inputs ok | tests <n> passed | no jobs submitted`

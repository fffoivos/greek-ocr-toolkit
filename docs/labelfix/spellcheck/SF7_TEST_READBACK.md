# RB8 — TR2 job 3702849 test/dev readback

20 October 2026. **Readback passed; candidate status unchanged.** `ssh clariden true` exited 0, with no certificate refresh. Slurm job and all recorded steps are `COMPLETED`, exit `0:0`. The complete job log is retained locally. No submission, resubmission, job-output modification, audit acceptance, label binding, or `.git` write was performed. Network use was limited to Clariden.

The release ID is `sf7_rc1_test_edits_A`, parent `google_raw_v2_import`, variant A, source job `3702849`. Both release receipts remain `candidate_pre_audit`, `bound: false`. This is integrity/readback evidence, not an accuracy audit.

| Split | Selected lines | Released rows | Edits | Composer corrected | Unchanged | HOLD | Composer-only rows omitted |
|---|---:|---:|---:|---:|---:|---:|---:|
| test | 28,620 | 308 | 341 | 319 | 3,592 | 24,709 | 11 |
| dev | 8,110 | 51 | 51 | 55 | 754 | 7,301 | 4 |

There are 377 distinct row byte patches for 392 logical edits: multiple mark edits can share a grapheme patch. Each row reconstructs forward and backward against its raw-parent UTF-8 bytes. Every edit has nonempty byte patches, valid parent spans, source/policy provenance, and an independent reversible application. All 36,730 selected labels equal their matching raw-parent labels. Full overlay coverage equals the exact TR1 selected ID inventories, controls equal corrected ∪ unchanged, and test/dev IDs are disjoint; no duplicate or unselected IDs occur. Separate score receipts report 28,620/28,620 and 8,110/8,110 alignment identity matches, with zero mismatches; their score-file hashes were verified remotely.

**Receipt terminology caveat:** all 11 test + 4 dev IDs in the upstream `normalization_only` fields actually differ by one composer-only insertion of U+201C (`“`). They are not Unicode-normalization-only changes. Independent comparison records each ID and difference in the readback receipt. They are excluded from the edits-only files, exactly as the existing converter emitted them. The upstream receipts and package were preserved; this terminology discrepancy is left visible for the audit.

## Edits by kind and head

“Insert” below corresponds to receipt kind `addition`, “delete” to `deletion`, and “substitute” to `substitution`. Quote-alias consumption is reported separately, rather than counted as a diacritic deletion.

| Split | Head | Insert | Delete | Substitute | Quote-alias consume |
|---|---|---:|---:|---:|---:|
| test | accent | 27 | 0 | 198 | 0 |
| test | breathing | 23 | 0 | 73 | 0 |
| test | dialytika | 1 | 0 | 0 | 0 |
| test | subscript | 17 | 0 | 0 | 0 |
| test | quote_alias | 0 | 0 | 0 | 2 |
| dev | accent | 6 | 0 | 32 | 0 |
| dev | breathing | 3 | 0 | 8 | 0 |
| dev | dialytika | 0 | 0 | 0 | 0 |
| dev | subscript | 2 | 0 | 0 | 0 |
| dev | quote_alias | 0 | 0 | 0 | 0 |

Totals: test 68 insertions, 0 diacritic deletions, 271 substitutions, 2 quote-alias consumptions; dev 11 insertions, 0 deletions, 40 substitutions.

## Rate comparison and runtime

| Release | Selected lines | Edited rows | Edits | Edits / selected line | Edits / 1,000 selected lines | Relative to train |
|---|---:|---:|---:|---:|---:|---:|
| Train RB7 | 124,669 | 605 | 665 | 0.00533412 | 5.3341 | 1.000× |
| test | 28,620 | 308 | 341 | 0.01191474 | 11.9147 | 2.234× |
| dev | 8,110 | 51 | 51 | 0.00628853 | 6.2885 | 1.179× |
| Test + dev | 36,730 | 359 | 392 | 0.01067247 | 10.6725 | 2.001× |

The denominator is the full selected population, including HOLD. These rates describe emitted candidate edits, not accuracy or a like-for-like precision comparison across populations.

Slurm allocation: **29m32s (1,772 s), four GPUs, 1.968889 allocated GPU-h**. Pipeline receipt: 1761.069 s (29m21.07s). Against the 40-minute / 2.666667 GPU-h forecast, allocation elapsed was **10m28s shorter (26.17% below forecast)**, saving 0.697778 allocated GPU-h. Requested limit was 60 minutes. GPU-h measures reserved GPUs × allocation elapsed, not measured GPU utilisation; queue delay is excluded. [Slurm state](../../../artifacts/sf7_rc1_test/output_3702849/job_state.txt).

## Identity and SHA verification

| Binding | SHA-256 |
|---|---|
| Policy digest | `f41e05636d165f1d15edbdb4f2bb6c1aa46721962a96302be8c4dce7ce305047` |
| Preregistration | `64a84ed0c8799026d44f066570b54075e9b9d1fbca8e2f099cfc9e9451189b2d` |
| Test parent | `e7a4f4025adde53b8a5e7894f87bde3b12d7730e893d2f1b78dc4e78b83c00f8` |
| Dev parent | `d462edac43e806ab87fac65860a3531cc9181d1c90a637d9e42eb45ca1940d17` |
| Test selection | `27467ca294bbbc28c576dc2fffa77bac82f125705691315eaaa36787156a0797` |
| Dev selection | `cd782de7dd39cb8c857eb24dfb4ae6720e05d16bededa64d1ae4d40be4d16c78` |

All **3,522 remote files** (8,984,710,474 bytes) were SHA-256 hashed; 3,498 distinct files match existing job-receipt references through 10,172 checks. Scalar metadata links and alignment-binding content were checked separately. The two recompose configs also match their SF7 receipt hashes. The remaining 22 files are metadata/receipt roots or summaries for which the job publishes no hash in another receipt; their captured hashes are retained without inventing an original receipt binding. Both raw-parent hashes, exact TR1 inventories, selection hashes, release hashes, policy-source hashes and preregistration were checked against the package. Local config hash equals the remote config hash. Each downloaded original output and the job log matches its remote SHA. The terminal log receipt equals `receipt.json`.

The independent local verifier uses the TR2 `readback_dryrun.py` forward/reverse method at full population scale, with RB7 provenance and untouched-byte checks. Compact witnesses were streamed directly from raw parents, selections, overlays and controls on Clariden; full raw files and overlays were not downloaded. The extractor and witness hash are retained for reproducibility. No inference or training ran on the Mac.

## Retained files and lead handoff

The local output directory contains **13,023,867 bytes (13.02 MB)**, below the 200 MB total limit. It contains both edits-only releases, all job receipts and small stage summaries, the complete log, Slurm state, compact readback witnesses, verification evidence and the RB7-schema [READBACK_RECEIPT.json](../../../artifacts/sf7_rc1_test/output_3702849/READBACK_RECEIPT.json).

**2,334 files / 8,980,420,534 bytes stay remote**, including raw production arrays, detector window arrays, alignment/frame scores, combined A/B/E runtime, shard overlays and full overlays/controls. Every retained-remote output path, size and SHA is listed in [REMOTE_ONLY_SHA256.json](../../../artifacts/sf7_rc1_test/output_3702849/REMOTE_ONLY_SHA256.json), relative to `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_sf7_test_20261019/output_3702849`. Raw parents, checkpoints and crops also remain remote as package inputs; their bindings are in the package and verification checks. These inputs are not part of the output-tree byte total.

The exact lead commit list is [LEAD_COMMIT_PATHS.txt](../../../artifacts/sf7_rc1_test/LEAD_COMMIT_PATHS.txt). It includes this report, the five readback/retrieval/verification scripts plus report generator, both releases, receipts, small summaries and all evidence files. Some artifact paths may be ignored by repository rules; the lead should use the exact list when staging. No staging or commit was attempted. Re-run local readback with:

```bash
python3 -B artifacts/sf7_rc1_test/validate_rb8.py
```

RB8 DONE: job 3702849 COMPLETED; test rows 308 edits 341; dev rows 51 edits 51; readback ok
